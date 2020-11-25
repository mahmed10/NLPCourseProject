from serpapi import GoogleSearch
search = GoogleSearch({"q": "Coffee", "location": "Austin,Texas"})
search_result = search.get_dictionary()
search_id = search_result.get("search_metadata").get("id")
print(search_result)