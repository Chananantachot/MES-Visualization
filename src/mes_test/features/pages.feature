Feature: MES Home page

  Scenario: Check if MES Home page works
    Given login form endpoint is "/signin" 
    And the following form data:
          | email | scott@mail.com |
          | password | hakxoz-7boFba-fynhyd |
    When submit the login form using POST
    Then page response status code should be 200
    And  page response body should contain "Welcome to Manufacturing Execution System (MES) Simulation" 

  Scenario: Check if MES Production Rates page works
    Given login form endpoint is "/signin" 
    And the following form data:
          | email | scott@mail.com |
          | password | hakxoz-7boFba-fynhyd |
    When submit the login form using POST
    Then page response status code should be 200
    And page response body should contain "Welcome to Manufacturing Execution System (MES) Simulation"   
    When i make a request to "/productionRates"
    Then page response status code should be 200
    And page response body should contain "Visualization of MES Production Rate Simulation"
    And page response body should contain "<canvas"

  Scenario: Check if MES Motor Speed page works
    Given login form endpoint is "/signin" 
    And the following form data:
          | email | scott@mail.com |
          | password | hakxoz-7boFba-fynhyd |
    When submit the login form using POST
    Then page response status code should be 200
    And page response body should contain "Welcome to Manufacturing Execution System (MES) Simulation"   
    When i make a request to "/motor"
    Then page response status code should be 200
    And page response body should contain "Motor Speed vs Temperature (AI Analysis)"
    And page response body should contain "<canvas"

  Scenario: Check if MES Motor Speed page works
    Given login form endpoint is "/signin" 
    And the following form data:
          | email | scott@mail.com |
          | password | hakxoz-7boFba-fynhyd |
    When submit the login form using POST
    Then page response status code should be 200
    And page response body should contain "Welcome to Manufacturing Execution System (MES) Simulation"   
    When i make a request to "/senser"
    Then page response status code should be 200
    And page response body should contain "Sensor Degradation Factors (AI Analysis)"
    And page response body should contain "<canvas"        