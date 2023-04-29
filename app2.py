#Versão sem ordenar por ano de lançamento.
import json
import requests
import re
from imdb import IMDb
from google.oauth2 import service_account
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuração da API IMDb
ia = IMDb()

# Configuração da API do Google Sheets
SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheet_id = '1FMNv5iYS6OBghPmChKrpAW1Ql1FRVD9NmaA4qGw2opc'
sheet_name = 'NET'

def get_imdb_movie_details(movie_id):
    movie = ia.get_movie(movie_id)
    genres = ", ".join(movie.get("genres", []))
    plot = movie.get("plot", [""])[0].split("::")[0]
    return genres, plot

def get_top_imdb_movies(start_year, end_year, num_movies):
    url = 'https://www.imdb.com/search/title/?groups=top_1000&sort=user_rating'
    headers = {'Accept-Language': 'en-US,en;q=0.8'}
    movies_list = []
    movies_count = 0

    with requests.Session() as s:
        while movies_count < num_movies:
            response = s.get(url, headers=headers)
            page_html = response.text
            soup = BeautifulSoup(page_html, 'html.parser')
            movies = soup.find_all("div", class_="lister-item mode-advanced")
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for movie in tqdm(movies, desc="Fetching movie details", total=len(movies)):
                    title = movie.find("img")["alt"]
                    release_year = int(re.search(r'\d+', movie.find("span", class_="lister-item-year text-muted unbold").text).group())
                    rating = float(movie.find("div", class_="inline-block ratings-imdb-rating")["data-value"])
                    movie_id = movie.find("a")["href"].split("/")[2]
                    numeric_movie_id = movie_id[2:]  # Remove 'tt' from the start

                    if release_year >= start_year and release_year <= end_year:
                        future = executor.submit(get_imdb_movie_details, numeric_movie_id)
                        futures.append((future, [title, release_year, rating, numeric_movie_id]))
                        movies_count += 1

                    if movies_count >= num_movies:
                        break
            
            for future, movie in futures:
                movie_details = future.result()
                movie.extend(movie_details)
                movies_list.append(movie)

            if movies_count >= num_movies:
                break

            next_page_link = soup.find_all("a", class_="lister-page-next next-page")
            if not next_page_link:
                break
            url = 'https://www.imdb.com' + next_page_link[-1]['href']
            
    return movies_list

def main():
    start_year = 2021
    end_year = 2023
    num_movies = 50  # Fetch top 50 movies
    movie_data = get_top_imdb_movies(start_year, end_year, num_movies)
    movie_data.sort(key=lambda x: (-x[1] if x[1] is not None else 0, -x[2]))  # Sort by year and rating in descending order
  
    update_google_sheet(movie_data)

def update_google_sheet(data):
    service = build('sheets', 'v4', credentials=creds)
    range_name = f'{sheet_name}!A2'
    body = {
        'range': range_name,
        'values': data,
        'majorDimension': 'ROWS'
    }

    request = service.spreadsheets().values().update(spreadsheetId=sheet_id, range=range_name, valueInputOption='RAW', body=body)
    response = request.execute()
    print(f'Successfully updated Google Sheet: {response}')

if __name__ == '__main__':
    main()

