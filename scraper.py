import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup as bs
from collections import Counter
import string
import hashlib



class globalVars:
    # google says avg 600-700 words per website
    # manuscripts and articles 4 - 7k
    max_words_in_page = 15000 # approx 10k is 20 pages single spaced 12 pt should cover most cases in pages that we crawl

    # have var to keep track of all urls to know if i should crawl or not?
        # hash urls for better storage
    # i think atp just don't hash it just store the links as is ;-; even though it can get large
    url_hash = set()

    # simhash
    document_sim = set()

    # for seeing the page with the largest num of words
    max_words = 0

    # for 50 most common words
    word_freq = Counter()

    # num subdomain in ics.uci.edu domain
    ics_subdomain = {}

    # helps keep track of unique subdomains
    # maps main w/o path to a set the paths
    ics_subdomain_unique_counter = {}

def scraper(url, resp):
    links = extract_next_links(url, resp)
    print("in scraper:", links)
    return links

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # save url and webpage locally to ensure we can compare it with others to avoid traps/duplicate/near dupes
    print('hello')

    ret_list = []

    # defrag
    url = url.split("#")[0] 
    parsed_url = urlparse(url)
    # url = parsed_url._replace(fragment='').geturl()

    # first check if url is valid before doing anything
    if not is_valid(url):
        # check for absolute and relative url when we add to ret_list, assume everything passed as url is absolute 
        print("no valid", url)
        return ret_list


    if resp.status // 100 == 4 or resp.status == 204 or resp.status // 100 == 3 or resp.status // 100 == 5 or resp.status // 100 >= 6:
        # anything w/ 400 is an error and 204 is blank page
        # redirection also skip it for now
        return ret_list
    """
    elif resp.status // 100 == 3:
        # redirection
        # 301 - moved permamently
        # if resp.status == 301:
        #     pass
        match resp.status:
            case 300:
                # multiple choice
                pass
            case 301:
                # moved permamently
                pass
            case 302:
                # found under diff URI
                pass
            case 303:
                # URI and SHOULD be retrieved using a GET method on that resource
                pass
            case 304:
                # not modified
                pass
            case 305:
                # requested resource MUST be accessed through the proxy given by the Location field
                pass
            case 306:
                # unused no need for checking and code is reserved ( will never be here ) 
                pass
            case 307:
                # temp redirect - resides temporarily under a different URI
                pass
    """
    # 200, 201 202, 203, 205, 206 can be handled same since we get smth 
        # assume 201 does send the info eventually since we have contents
    # .raw_response does not have redirection information i think so skip for now
    
    # valid page
    # BeautifulSoup - tool for webscrapping - does a lot of stuff lol
    soup = bs(resp.raw_response.content, "html.parser")
    
    # print(soup.prittify()) # html of the page
    # want <a> tag since hyperlink
    hyperlinks = soup.find_all("a")

    # first do textual analysis to ensure not dupe
    text = soup.get_text()
    print("Look at text", text)
    if ( len(text) > globalVars.max_words * 10):
        # so we don't end up doing calculations for needlessly long docs taking into account of stopwords
        print("Too many words:", len(text))
        return ret_list

    # make sure end. and end are counted as the same thing
    text = ''.join(char for char in text if char not in string.punctuation)


    word_list = text.split()

    globalVars.max_words = max(len(text), globalVars.max_words)
    print("max_words:", globalVars.max_words)
    # avoid large pages 
    if len(word_list) > globalVars.max_words_in_page:
        return ret_list

    # weighted words
    word_list = [word for word in word_list if word not in stop_words] 
    

    # check similarity first before updating word_freq
    curr_sim_hash = simhash(word_list)
    if curr_sim_hash in globalVars.document_sim:
        # exact duplicate 
        return ret_list
    # compute similarity for all in docsim ig
    for i in globalVars.document_sim:
        similarity = 1 - bin(i ^ curr_sim_hash).count('1') / 128
        if similarity > 0.932:
            # 90% 
            return ret_list

    # not super similar with anything, so add to set so we can compare others to it
    globalVars.document_sim.add(curr_sim_hash)

    # now update counter
    weighted_words = Counter(word_list)
    globalVars.word_freq.update(weighted_words)
    # print("word_freq:", globalVars.word_freq)

    # now we can extract the links finally lol
    # make sure to check for duplicates here so we dont have to simhash yada yada

    links = set()
    # since i check valid first thing in extract, no need to check again here
    for link in hyperlinks:
        if link.has_attr("href"):
            url2 = link.get("href")
            # url can be a relative url!
            if url2.startswith("www."):
                url2 = "https://" + url2
            new_parse = urlparse(url2)

            # if it has scheme then we r good as absolute?
            # if it starts with // then have our url be http or smth so we are consistent
            if not new_parse.hostname:
                # doesn't start with // and no http yada yada
                url2 = f"{parsed_url.scheme}://{parsed_url.hostname}/{new_parse.path}"
            elif url2.startswith("//"):
                url2 = f"{parsed_url.scheme}://{parsed_url.hostname}/{new_parse.hostname}"
            else:
                # to get rid of all other stuff pretty sure not necessary this also defragments it which i do somewhere too
                # honestly don't want to make it into http or https since it might affect smth but for checkings but eventually
                # wait can just check it in is_valid if the https or http version is in there?
                # might lead to complications w/ above since if we call it again, is_valid will return false
                url2 = f"{new_parse.scheme}://{new_parse.hostname}/{new_parse.path}"
            links.add(url2)
    
    return list(links)

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    try:
        parsed = urlparse(url)

        # smth check to make sure our code is right
        valid_domains = [".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu"]
        j = 0

        

        
        for i in valid_domains:
            if re.search(i, url):
                break
            j += 1

        if j == 4:
            return False
        



        # moved up since we want these schemes
        if parsed.scheme not in set(["http", "https"]):
            print("In parsed.scheme http")
            return False
        

        if re.search(valid_domains[0], url):
            # ics domain
            # scheme should not matter as http and https lead to same? so we can ignore it 
            # printing, lets just print in all http
            hostname = parsed.hostname.lower()
            path = parsed.path.rstrip('/')

            # if hostname isnt even in counter hostname should be like vision.ics.uci.edu
            if "informatics.uci.edu" not in hostname:
                if hostname not in globalVars.ics_subdomain:
                    globalVars.ics_subdomain[hostname] = 1

                    # if not in there also not in the helper
                    globalVars.ics_subdomain_unique_counter[hostname] = {path}
                    
                else:
                    # have to do checking to see if its unique
                    if path not in globalVars.ics_subdomain_unique_counter[hostname]:
                        globalVars.ics_subdomain[hostname] += 1
                        globalVars.ics_subdomain_unique_counter[hostname].add(path)
            
            # otherwise its not unique so don't count it

        # moved up since we always want to add a unique url within the domains
        temp = shorten_and_hash(url)

        if temp in globalVars.url_hash:
            print("temp in urlhash")
            return False
        # want to add here since unique urls only care about if in domain
        # all urls passed in are defragmented too
        # also add the http or https version of it
        # wait my func already makes it so we dont have http or https we should be good
        globalVars.url_hash.add(temp)
        
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv|ppt|json|log|xml|ics"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False
        return True

    except TypeError:
        print ("TypeError for ", parsed)
        raise

words_copied = """a
about
above
after
again
against
all
am
an
and
any
are
aren't
as
at
be
because
been
before
being
below
between
both
but
by
can't
cannot
could
couldn't
did
didn't
do
does
doesn't
doing
don't
down
during
each
few
for
from
further
had
hadn't
has
hasn't
have
haven't
having
he
he'd
he'll
he's
her
here
here's
hers
herself
him
himself
his
how
how's
i
i'd
i'll
i'm
i've
if
in
into
is
isn't
it
it's
its
itself
let's
me
more
most
mustn't
my
myself
no
nor
not
of
off
on
once
only
or
other
ought
our
ours
ourselves
out
over
own
same
shan't
she
she'd
she'll
she's
should
shouldn't
so
some
such
than
that
that's
the
their
theirs
them
themselves
then
there
there's
these
they
they'd
they'll
they're
they've
this
those
through
to
too
under
until
up
very
was
wasn't
we
we'd
we'll
we're
we've
were
weren't
what
what's
when
when's
where
where's
which
while
who
who's
whom
why
why's
with
won't
would
wouldn't
you
you'd
you'll
you're
you've
your
yours
yourselfves"""
stop_words = set(words_copied.split("\n"))

# taken from A1
# compute frequencies and making sure we don't count the stop words
# i dont think i even use this lol
def word_freq_idk( tokens: list ) -> dict:
    my_dict = {}
    for i in tokens:
        if i not in stop_words:
            try:
                my_dict[i] += 1
            except:
                my_dict[i] = 1
    return my_dict

# url normalizer so hashing yields consistent results
# no longer hashes
def shorten_and_hash(url):
    parsed_url = urlparse(url)

    # lowercase since not case sensitive
    # scheme = parsed_url.scheme.lower() is_valid already checks if it is http and https
    
    hostname = parsed_url.hostname.lower()


    path = parsed_url.path.rstrip('/')

    # Reconstruct the normalized URL
    normalized_url = f"https://{hostname}{path}"


    return normalized_url

def simhash(tokens, hash_size = 128):

    hash_vector = [0] * hash_size

    for token in tokens:
        # md5 returns hex hash so gotta properly convert it
        token_hash = int(hashlib.md5(token.encode()).hexdigest(), 16)
        for i in range(hash_size):
            # right most bit
            hash_bit = (token_hash >> i) & 1
            hash_vector[i] += 1 if hash_bit else -1

    # create the simhash vector thing 101010101010101....
    simhash_signature = 0
    for i in range(hash_size):
        if hash_vector[i] > 0:
            simhash_signature |= 1 << i

    # confirmed does work i think can check sim w/ print( 1 - bin(simhash1 ^ simhash2).count('1') / 128) where 128 is the bin_size 
    # if similarity is like 95% then we have prob i think
    return simhash_signature