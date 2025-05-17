Feature: Analyze production slowdown

  Scenario: Generate production slowdown table and summary
    Given the production slowdown function is executed
    Then the output should include an HTML table
    And the summary should contain impact levels
