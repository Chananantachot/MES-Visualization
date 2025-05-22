Feature: MES Register page

  Scenario: Check if MES register page works
    Given the MES register app is running
    When I request the "/register" endpoint
    Then I should receive "Register account"

  Scenario: Check if do Submit valid user to register page works
    Given the register form endpoint is "/register"
    And the following register form data:
          | fullname | tester testing |
          | email    | test@mail.com |
          | password | qubxo8-xaqwyp-wusMej |
    When I submit the register form using POST    
    Then the register response status code should be 200
    And the register response body should contain "Account created successfully." and "userid" value in hidden field

  Scenario: Check if do Submit empty user to register page works
      Given the register form endpoint is "/register"
      And the following register form data:
            | fullname |  |
            | email    |  |
            | password |  |
      When I submit the register form using POST    
      Then the register response status code should be 200
      And the register response body should contain "Please fill in all fields."  

  Scenario: Check if do Submit existing user to register page works
    Given the register form endpoint is "/register"
    And the following register form data:
          | fullname | tester2 existing |
          | email    | test@mail.com |
          | password | qubxo8-xaqwyp-wusMej |
    When I submit the register form using POST    
    Then the register response status code should be 200
    And the register response body should contain "test@mail.com already exists"  