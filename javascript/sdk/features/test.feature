Feature: Is this CVE?

  Scenario: Search the NVD for a keyword
    Given I have a keyword to search for "CVE-2023-26331"
    When I search for the keyword using the search method
    Then the response should be a SearchResults object