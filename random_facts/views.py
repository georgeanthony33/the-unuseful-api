from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
import requests
import time
import six
from google.cloud import translate_v2 as translate

def get_random_fact():
    response = requests.get('https://randomuselessfact.appspot.com/random.json?language=en')
    return response

def unique(list):
    unique_list = []

    for x in list:
        if x not in unique_list:
            unique_list.append(x)
        else:
            continue
    return len(unique_list)

def streamline_fact_json(fact):
    fact.pop('source', None)
    fact.pop('source_url', None)
    fact['url'] = fact['permalink'] + '.json'
    fact.pop('permalink', None)
    return fact
    
class RandomFactsListView(View):

    def get(self, request):

        all_random_facts = []
        iterations = 1000

        try:
            while len(all_random_facts) < iterations:
                response = get_random_fact()

                if response.status_code == 200:
                    all_random_facts.append(response.json())
                elif response.status_code == 429:
                    retry_after = int(response.headers['Retry-After']) + 1
                    fact_ids = list(map(lambda fact: fact['id'], all_random_facts))
                    random_facts_status = {
                        'status': '429 ERROR',
                        'message': f'too many requests - waiting {retry_after} seconds until next API call',
                        'facts': {
                            'total': len(all_random_facts),
                            'unique': unique(fact_ids)
                        }
                    }
                    print(random_facts_status)
                    time.sleep(retry_after)
                    continue
                elif int(str(response.status_code)[0]) in [4, 5]:
                    raise Exception("API error")
                
                if len(all_random_facts) % 10 == 0:
                    fact_ids = list(map(lambda fact: fact['id'], all_random_facts))
                    random_facts_status = {
                        'status': 'LOADING',
                        'message': None,
                        'facts': {
                            'total': len(all_random_facts),
                            'unique': unique(fact_ids)
                        }
                    }
                    print(random_facts_status)

            fact_ids = list(map(lambda fact: fact['id'], all_random_facts))
            random_facts_status = {
                'status': 'COMPLETED',
                'message': None,
                'facts': {
                    'total': len(all_random_facts),
                    'unique': unique(fact_ids)
                }
            }

            print(random_facts_status)
            return JsonResponse(random_facts_status)

        except Exception as err:
            raise

class RandomFactIds(View):

    def get(self, request):

        all_random_facts = []
        iterations = 1000

        try:
            while len(all_random_facts) < iterations:
                response = get_random_fact()

                if response.status_code == 200:
                    all_random_facts.append(response.json())
                elif response.status_code == 429:
                    retry_after = int(response.headers['Retry-After']) + 1
                    print(f'Waiting {retry_after} seconds until next API call')
                    time.sleep(retry_after)
                    continue
                elif int(str(response.status_code)[0]) in [4, 5]:
                    raise Exception("API error")

                if len(all_random_facts) % 10 == 0:
                    print('LOADING DATA')

            fact_ids = list(map(lambda fact: fact['id'], all_random_facts))

            print('DATA LOADED', fact_ids)
            return JsonResponse(fact_ids, safe=False)

        except Exception as err:
            raise

class RandomFactDetailView(View):

    def get(self, *args, **kwargs):
        
        try:    
            response = requests.get(f"http://randomuselessfact.appspot.com/{kwargs['slug']}.json")
            if response.status_code == 404:
                raise FileNotFoundError('Fact not found')
            elif response.status_code == 429:
                retry_after = int(response.headers['Retry-After']) + 1
                print(f'429 Error - next API call in {retry_after} seconds')
                time.sleep(retry_after)
                response = requests.get(f"http://randomuselessfact.appspot.com/{kwargs['slug']}.json")
            elif int(str(response.status_code)[0]) in [4, 5]:
                raise Exception("API error")

            json_response = response.json()
            streamlined_fact = streamline_fact_json(json_response)

            print(streamlined_fact)
            return JsonResponse(streamlined_fact)

        except FileNotFoundError:
            raise
        except Exception:
            raise

class TranslatedFactDetailView(View):

    def get(self, *args, **kwargs):
        try:    
            response = requests.get(f"http://randomuselessfact.appspot.com/{kwargs['id']}.json")
            
            if response.status_code == 404:
                raise FileNotFoundError('Fact not found')
            elif response.status_code == 429:
                retry_after = int(response.headers['Retry-After']) + 1
                print(f'429 Error - next API call in {retry_after} seconds')
                time.sleep(retry_after)
                response = requests.get(f"http://randomuselessfact.appspot.com/{kwargs['id']}.json")
            elif int(str(response.status_code)[0]) in [4, 5]:
                raise Exception("API error")

            json_response = response.json()
            text = json_response['text']
            source_language = json_response['language']
            target_language = kwargs['lang']

            if source_language != target_language:
                translate_client = translate.Client.from_service_account_json(
                    'unuseful-api.json')

                if isinstance(text, six.binary_type):
                    text = text.decode("utf-8")

                try:
                    result = translate_client.translate(text, source_language=source_language, target_language=target_language)
                except:
                    raise Exception("Translation error")
                streamlined_fact = streamline_fact_json(json_response)
                streamlined_fact['text'] = result["translatedText"]
                streamlined_fact['language'] = target_language
            else:
                streamlined_fact = streamline_fact_json(json_response)

            print(streamlined_fact)
            return JsonResponse(streamlined_fact)
            
        except FileNotFoundError:
            raise
        except Exception:
            raise