import requests

API_URL = "https://nomad-movies.nomadcoders.workers.dev/movies"


def fetch_movies():
    """API에서 영화 목록을 가져옵니다."""
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json()


def search_movies(movies, query):
    """제목 또는 개요에서 검색어로 필터링합니다."""
    query_lower = query.lower()
    return [
        m for m in movies
        if query_lower in m.get("title", "").lower()
        or query_lower in m.get("overview", "").lower()
    ]


def print_movie(movie):
    """영화 정보를 한 줄로 출력합니다."""
    title = movie.get("title", "N/A")
    release = movie.get("release_date", "N/A")
    rating = movie.get("vote_average", "N/A")
    print(f"  - {title} ({release}) | 평점: {rating}")


def main():
    print("영화 데이터 로딩 중...")
    movies = fetch_movies()
    print(f"총 {len(movies)}편 로드됨.\n")

    # 검색어 입력 (빈 문자열이면 전체 출력)
    query = input("검색어 입력 (Enter = 전체 목록): ").strip()

    if query:
        results = search_movies(movies, query)
        print(f"'{query}' 검색 결과: {len(results)}편\n")
    else:
        results = movies
        print("전체 목록:\n")

    for movie in results:
        print_movie(movie)


if __name__ == "__main__":
    main()