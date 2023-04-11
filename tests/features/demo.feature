Feature: Demo Experience
    Test common scenarios for demo users

    Background: Set up Demo user
        Given I am signed in as a demo user

    # Activity data
    Scenario: Get logs
        Given I want to request activity data from the "logs" view
        When I retrieve the activity data
        Then the response should contain logs

    Scenario Outline: Get logs for specific test
        Given I want to request activity data from the "logs" view
        And I specify a test ID <test>
        When I retrieve the activity data
        Then the response should contain logs
        And the response should contain data only for that test ID

        Examples:
            | test                                   |
            | "39de298a-911d-4a3b-aed4-1e8281010a9a" |
            | "ca9b22be-93d5-4902-95f4-4bc43a817b73" |
            | "b74ad239-2ddd-4b1e-b608-8397a43c7c54" |

    Scenario Outline: Get logs for specific DOS
        Given I want to request activity data from the "logs" view
        And I specify a DOS <dos>
        When I retrieve the activity data
        Then the response should contain logs
        And the response should contain data only for that DOS

        Examples:
            | dos              |
            | "linux-x86_64"   |
            | "windows-x86_64" |
            | "darwin-arm64"   |
            | "darwin-x86_64"  |

    Scenario Outline: Get logs for specific tag
        Given I want to request activity data from the "logs" view
        And I specify a tag <tag>
        When I retrieve the activity data
        Then the response should contain logs
        And the response should contain data only for that tag

        Examples:
            | tag           |
            | "server"      |
            | "container"   |
            | "workstation" |

    Scenario Outline: Get logs with complex options
        Given I want to request activity data from the "logs" view
        And I specify a test ID <test>
        And I specify a tag <tag>
        And I specify a DOS <dos>
        When I retrieve the activity data
        Then the response should contain logs
        And the response should contain data only for that test ID
        And the response should contain data only for that tag
        And the response should contain data only for that DOS

        Examples:
            | test                                   | tag           | dos              |
            | "39de298a-911d-4a3b-aed4-1e8281010a9a" | "container"   | "linux-x86_64"   |
            | "2e705bac-a889-4283-9a8e-a12358fa1d09" | "server"      | "windows-x86_64" |
            | "39de298a-911d-4a3b-aed4-1e8281010a9a" | "workstation" | "darwin-x86_64"  |

    Scenario: Get insights
        Given I want to request activity data from the "insights" view
        When I retrieve the activity data
        Then the response should contain insights

    Scenario: Get probes
        Given I want to request activity data from the "probes" view
        When I retrieve the activity data
        Then the response should contain probes

    Scenario: Get rules
        Given I want to request activity data from the "rules" view
        When I retrieve the activity data
        Then the response should contain rules

    # Tests
    Scenario: Get tests
        When I retrieve tests
        Then the response should contain tests

    # Searching
    Scenario Outline: Search the NVD for a keyword
        Given I have a keyword to search for <keyword>
        When I search for the keyword
        Then the response should contain search results

        Examples:
            | keyword          |
            | "CVE-2021-1234"  |
            | "CVE-2022-22965" |
            | "CVE-2017-7494"  |