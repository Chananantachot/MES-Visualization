Feature: Analyze Machine Health

  Scenario: Generate machine health table and summary
    Given the machine health function is executed
    Then the machine health output should include an HTML table
    And the summary should contain Failure Risk
