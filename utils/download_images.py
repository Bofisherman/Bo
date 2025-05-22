from duckduckgo_search import DDGS
import requests
import os


def download_images(query, folder, max_results=10):
    os.makedirs(folder, exist_ok=True)
    with DDGS() as ddgs:
        results = ddgs.images(query, max_results=max_results)
        for i, result in enumerate(results):
            try:
                img_data = requests.get(result['image']).content
                with open(os.path.join(folder, f"{i}.jpg"), 'wb') as f:
                    f.write(img_data)
            except Exception:
                continue


download_images("salmon fish", "fish_dataset/salmon", max_results=20)
download_images("tuna fish", "fish_dataset/tuna", max_results=20)
download_images("clownfish", "fish_dataset/clownfish", max_results=20)
