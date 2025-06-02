import requests

    
def get_random_dog_image():
    url = "https://dog.ceo/api/breeds/image/random"
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()
        
        if data.get("status") == "success":
            return data["message"]
        else:
            print("Dog API error: Unexpected response format")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Dog API request error: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Error parsing Dog API response: {e}")
        return None


def get_cat_fact():
    url = 'https://catfact.ninja/fact'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['fact']
    except requests.exceptions.RequestException as e:
        print(f"Cat Facts API error: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Error parsing Cat Facts API response: {e}")
        return None
