import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from requests.utils import requote_uri
from . import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import SearchSerializer

BASE_CRAIGSLIST_URL = 'https://losangeles.craigslist.org/search/?query={}'
#BASE_IMAGE_URL = 'https://images.craigslist.org/{}_300x300.jpg'


def home(request):
    return render(request, 'base.html')

def new_search(request):
    search = request.POST.get('search')
    search=search.lower()
    models.Search.objects.get_or_create(search=search)
    final_url = BASE_CRAIGSLIST_URL.format(requote_uri(search))
    response = requests.get(final_url)
    data = response.text
    soup = BeautifulSoup(data, features='html.parser')

    post_listings = soup.find_all('li', {'class': 'result-row'})

    final_postings = []

    for post in post_listings:
        post_title = post.find(class_='result-title').text
        post_url = post.find('a').get('href')

        if post.find(class_='result-price'):
            post_price = post.find(class_='result-price').text
        else:
            post_price = 'N/A'

        #if post.find(class_='result-image').get('data-ids'):
        #    post_image_id = post.find(class_='result-image').get('data-ids').split(',')[0].split(':')[1]
        #    post_image_url = BASE_IMAGE_URL.format(post_image_id)
        #    print(post_image_url)
        #else:
        #    post_image_url = 'https://craigslist.org/images/peace.jpg'

        final_postings.append((post_title, post_url, post_price))

    stuff_for_frontend = {
        'search': search,
        'final_postings': final_postings,
    }

    return render(request, 'my_app/new_search.html', stuff_for_frontend)

@api_view(['GET'])
def search_coll(request):
    if request.method=="GET":
        search=models.Search.objects.all()
        serializer=SearchSerializer(search,many=True)
        return Response(serializer.data)