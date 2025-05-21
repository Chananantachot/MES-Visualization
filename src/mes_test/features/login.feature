Feature: MES Login page

  Scenario: Check if MES Login page works
    Given the MES Login app is running
    When I request the "/signin" endpoint
    Then I should receive "Sign in to continue to Fake it easy"

  Scenario: Check if do Submit un-registered login user to login page works
    Given the form endpoint is "/signin"
    And the following form data:
        | email | invalid_user@mail.com |
        | password | secret123 |
    When I submit the form using POST    
    Then the response status code should be 200
    And the response body should contain "Invalid username or password!"  


  Scenario: Check if do Submit registered login user to login page works
    Given the form endpoint is "/signin"
    And the following form data:
          | email | someone@mail.com |
          | password | qubxo5-saqwyp-wusMej |
    When I submit the form using POST    
    Then the response status code should be 200
    And the response body should contain "Welcome to Manufacturing Execution System (MES) Simulation"  