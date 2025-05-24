Feature: MES ALL pages
  Scenario: Check if MES Home page works
    Given the form endpoint is "/signin" 
    And the following form data:
          | field | value |
          | email | scott@mail.com |
          | password | hakxoz-7boFba-fynhyd |
    When I submit the form using POST 
    Then the response status code should be  200
    And the response body should contain "Welcome to Manufacturing Execution System (MES) Simulation" 

  Scenario: Check if MES Production Rates page works
    Given the form endpoint is "/signin" 
    And the following form data:
          | field | value |
          | email | scott@mail.com |
          | password | hakxoz-7boFba-fynhyd |
    When I submit the form using POST
    Then the response status code should be 200
    And the response body should contain "Welcome to Manufacturing Execution System (MES) Simulation"   
    When i make a request to "/productionRates"
    Then the response status code should be 200
    And the response body should contain "Visualization of MES Production Rate Simulation"
    And the response body should contain "<canvas"
  
  Scenario: Check if MES Production Rates REST API works
    Given the form endpoint is "/signin" 
    And the following form data:
          | field | value |
          | email | scott@mail.com |
          | password | hakxoz-7boFba-fynhyd |
    When I submit the form using POST 
    Then the response status code should be 200
    When I make a request to "/productionRates" API endpoint
    Then the response status code should be 200
    Then I should receive json data back

  Scenario: Check if MES Motor Speed page works
    Given the form endpoint is "/signin" 
    And the following form data:
          | field | value |
          | email | scott@mail.com |
          | password | hakxoz-7boFba-fynhyd |
    When I submit the form using POST 
    Then the response status code should be 200
    And the response body should contain "Welcome to Manufacturing Execution System (MES) Simulation"   
    When i make a request to "/motor"
    Then the response status code should be 200
    And the response body should contain "Motor Speed vs Temperature (AI Analysis)"
    And the response body should contain "<canvas"

  Scenario: Check if MES Motor Speed REST API works
    Given the form endpoint is "/signin" 
    And the following form data:
          | field | value |
          | email | scott@mail.com |
          | password | hakxoz-7boFba-fynhyd |
    When I submit the form using POST 
    Then the response status code should be 200
    When I make a request to "/motor" API endpoint
    Then the response status code should be 200
    Then I should receive json data back

  Scenario: Check if MES Sensor Degradation Factors works
    Given the form endpoint is "/signin" 
    And the following form data:
          | field | value |
          | email | scott@mail.com |
          | password | hakxoz-7boFba-fynhyd |
    When I submit the form using POST 
    Then the response status code should be 200
    And the response body should contain "Welcome to Manufacturing Execution System (MES) Simulation"   
    When i make a request to "/senser"
    Then the response status code should be 200
    And the response body should contain "Sensor Degradation Factors (AI Analysis)"
    And the response body should contain "<canvas"        

  Scenario: Check if MES Sensor Degradation Factors REST API works
    Given the form endpoint is "/signin" 
    And the following form data:
          | field | value |
          | email | scott@mail.com |
          | password | hakxoz-7boFba-fynhyd |
    When I submit the form using POST 
    Then the response status code should be 200
    When I make a request to "/senser" API endpoint
    Then the response status code should be 200
    Then I should receive json data back