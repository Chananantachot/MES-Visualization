Feature: JWT Authentication

  Scenario: User logs in and receives JWT token in cookies
    Given the login form endpoint is "/signin"
    And the following form data:
          | email | someone@mail.com |
          | password | qubxo5-saqwyp-wusMej |
    When I submit the login form using POST
    Then the response should contain a "Set-Cookie" header
    And the cookie "access_token_cookie" should be set
    And the cookie "access_token_cookie" should be set expried
    When I send a POST request to "/logout"
    Then the cookie "access_token_cookie" should not be present