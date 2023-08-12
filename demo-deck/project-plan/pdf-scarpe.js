const puppeteer = require('puppeteer');


const sleep = async (ms) => {
    return new Promise(resolve => setTimeout(resolve, ms));
}


async function searchBook(bookTitle) {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();

    // await page.goto('https://www.pdfdrive.to/');

    // await page.type("[name='search']", bookTitle);
    // await page.type('#q', bookTitle);
    // await page.keyboard.press('Enter');

    // await page.waitForNavigation();

    

//    const element = await page.$('.title-link');
  

   // Get href attribute of the element
//    const href = await page.evaluate(el => el.href, element);
//    console.log(`URL to navigate: ${href}`);
   
    // Navigate to the href
//    await page.goto(href);
   await page.goto(bookTitle);

    // const downloadElement = await page.$('a#download-button-link');
   const downloadElement = await page.$('.btn-download');
   
   // Get href attribute of the element
   const btnhref = await page.evaluate(el => el.href, downloadElement);
   console.log(`URL to navigate: ${btnhref}`);
   
    // Navigate to the href
   await page.goto(btnhref);
    
   // await page.waitForNavigation();
   await sleep(10000);

    // wait until "Checking for file health..." is gone
    // await page.waitForSelector('.download-btn', { hidden: true });
   const downloadBtn = await page.$('.download-btn');
   downloadBtn?.click();  
}

(async () => {
    const books = [
        'https://pdfdrive.to//download/the-daily-stoic-366-meditations-on-wisdom-perseverance-and-the-art-of-living',
        'https://pdfdrive.to//download/boundaries-when-to-say-yes-how-to-say-no-to-take-control-of-your-life',
        'https://pdfdrive.to//download/the-5-second-rule-transform-your-life-work-and-confidence-with-everyday-courage',
        'https://pdfdrive.to//download/you-are-a-badass-how-to-stop-doubting-your-greatness-and-start-living-an-awesome-life',
        'https://pdfdrive.to//download/the-gifts-of-imperfection-embrace-who-you-are',
        'https://pdfdrive.to//download/the-miracle-morning-the-not-so-obvious-secret-guaranteed-to-transform-your-life'
    ];
    
    for (let book of books) {
        searchBook(book);
    }
})();
