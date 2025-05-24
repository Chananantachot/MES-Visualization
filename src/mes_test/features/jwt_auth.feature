Feature: JWT Authentication

  Scenario: User logs in and receives JWT token in cookies
    Given the form endpoint is "/signin"
    And the following form data:
          | field | value |
          | email | scott@mail.com|
          | password | hakxoz-7boFba-fynhyd |
    When I submit the form using POST
    Then the response body should contain "Set-Cookie"
    And the cookie "access_token_cookie" should be set
    And the cookie "access_token_cookie" should be set expried
    When I send a POST request to "/logout"
    Then the cookie "access_token_cookie" should not be present