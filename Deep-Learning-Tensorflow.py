from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ProcessPoolExecutor as PPE, ThreadPoolExecutor as TPE
import time, pickle, requests, bs4, json, wget, re, os


browser = webdriver.Chrome()
browser.get('https://sso.teachable.com/secure/130400/users/sign_in')

page = browser.page_source
cookies = browser.get_cookies()

curriculumURL = browser.current_url
curriculumURL

browser.quit()

sesh = requests.Session()

for cookie in cookies:
    sesh.cookies.set(cookie['name'], cookie['value'])

curriculum_page = sesh.get(curriculumURL)
soup0 = bs4.BeautifulSoup(curriculum_page.content, 'html.parser')
topicTags = soup0.find_all(class_='row')


baseURL = 'https://365datascience.teachable.com'

def run(topicTag):
    topicIdx = topicTags.index(topicTag)
    
    topicTitle = topicTags[topicIdx].find(class_='section-title').text.split('Available')[0].strip()
    numVids = len(topicTags[topicIdx].find_all('li'))
    
    pathBase = f'Deep Learning in Tensorflow 2.0/{topicIdx+1}. {topicTitle}'
    
    if os.path.exists(pathBase):
        pass
    else:
        os.makedirs(pathBase)
    
    print(f'{topicIdx+1}: {topicTitle} ({numVids} videos)')    
    
    for vidIdx, vidTag in enumerate(topicTags[topicIdx].find_all('li')):
        vidTitle = vidTag.text.split('Start')[1].split('(')[0].strip()
        print(f'\t{vidIdx+1}: {vidTitle}')
        
        partialURL = vidTag.find('a')['href']
        vidURL = f'{baseURL}{partialURL}'
        print(f'\t{vidURL}')
        
        vidPage = sesh.get(vidURL)
        soup1 = bs4.BeautifulSoup(vidPage.content, 'html.parser')
        
        try:
            vidID = soup1.find(class_=re.compile(r'attachment-wistia-player.*'))['data-wistia-id']
            
            downloadPage = sesh.get(f'https://fast.wistia.net/embed/iframe/{vidID}?videoFoam=true')
            soup2 = bs4.BeautifulSoup(downloadPage.content, 'html.parser')
            
            target_script = str(soup2.findAll('script')[-1]).split('[')[2].split(']')[0]
            pattern = re.compile(r'(\{\"type\"\:\".+?\})(?!,\")')
            matches = re.findall(pattern, target_script)
            
            jsonInfo = json.loads(matches[1])
            print(f"\t{jsonInfo['display_name']}")
            
            filePath = f'{pathBase}/{vidIdx+1}. {vidTitle}.mp4'

            if os.path.exists(filePath):
                pass
            else:
                wget.download(jsonInfo['url'], filePath)
        except TypeError:
            print('NOOOOOOOOOOOOOOOO')


with TPE() as executor:
    executor.map(run, topicTags)

# with PPE() as executor:
#     executor.map(run, topicTags)