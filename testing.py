from urllib.parse import urlparse, urlunparse
import string
import hashlib
from bs4 import BeautifulSoup as bs

def defragment_url(url):
    # Parse the URL
    parsed_url = urlparse(url)

    # Remove the fragment component
    defragmented_url = parsed_url._replace(fragment='').geturl()

    return defragmented_url

# Example usage:
url = "http://example.com/page#section1"
defragmented = defragment_url(url)
print(defragmented)  # Output: http://example.com/page


temp = """
Example
This is a heading
This is a paragraph.
"""
temp = ''.join(char for char in temp if char not in string.punctuation)
print(temp.split())
text1 = "This is a sample document for testing."
text2 = "SimHash is a technique used for fingerprinting documents."
text3 = "SimHash is a technique used for fingerprinting documents documents."
text1 = ''.join(char for char in text1 if char not in string.punctuation)
text2 = ''.join(char for char in text2 if char not in string.punctuation)
text3 = ''.join(char for char in text3 if char not in string.punctuation)
def simhash(tokens, hash_size = 128):

    hash_vector = [0] * hash_size
    
    for token in tokens:
        # md5 returns hex so gotta properly convert it
        token_hash = int(hashlib.md5(token.encode()).hexdigest(), 16)
        # print(token_hash)
        for i in range(hash_size):
            hash_bit = (token_hash >> i) & 1
            hash_vector[i] += 1 if hash_bit else -1

    # Generate the SimHash signature
    simhash_signature = 0
    for i in range(hash_size):
        if hash_vector[i] > 0:
            simhash_signature |= 1 << i

    return simhash_signature

simhash1 = simhash(text1)
simhash2 = simhash(text2)
simhash3 = simhash(text3)
print( 1 - bin(simhash1 ^ simhash2).count('1') / 128)
print( 1 - bin(simhash1 ^ simhash1).count('1') / 128)
print( 1 - bin(simhash2 ^ simhash3).count('1') / 128)

html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Example Page</title>
</head>
<body>
    <h1>Example Page</h1>
    <p>This is a paragraph with <a href="https://www.example.com">a hyperlink</a>.</p>
    <p>Here's another paragraph with <a href="https://www.example.com/page2">another hyperlink</a>.</p>
    <p>And one more paragraph with <a href="https://www.example.com/page3">yet another hyperlink</a>.</p>
    <p>And one more paragraph with <a href="https://www.example.com/page3#2222">yet another hyperlink</a>.</p>
    <p>And one more paragraph with <a href="/page3#2222">yet another hyperlink</a>.</p>
</body>
</html>
"""
soup = bs(html, "html.parser")
hyperlinks = soup.find_all("a")
for link in hyperlinks:
    url = link.get("href")
    # note relative urls!
    parsed_url = urlparse(url)
    url = parsed_url._replace(fragment='').geturl()
    print(url)
    print(parsed_url.hostname)
    print(parsed_url)

# url = "http://vision.ics.uci.edu/example-page-1"
# parsed_url = urlparse(url)
# hostname = parsed_url.hostname

# print("Hostname:", hostname)
print()
print()

url = "www.stat.uci.edu/contact-the-department"
parsed_url = urlparse(url)
# url = "http://" + url
# parsed_url = urlparse(url)
print(parsed_url)

url = "http://www.ics.uci.edu//grad/admissions/index"
parsed_url = urlparse(url)
print(parsed_url)
