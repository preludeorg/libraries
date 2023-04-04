import { When, Then, Given } from "@cucumber/cucumber"

Given('I have a keyword to search for {string}', function (keyword) {
  this.keyword = keyword;
})

When('I search for the keyword using the search method', async function() {
  try {
    const service = new Service({
      host: 'https://api.staging.preludesecurity.com',
    })
    const response = await service.detect.search(this.keyword);
  } catch (err) {}
})

Then('the response should be a SearchResults object', function (response) {
  console.log(response)
})