Feature: MES Home page

  Scenario: Check if MES Home page works
    Given the MES app is running
    When I request the "/" endpoint
    Then I should receive "Welcome to Manufacturing Execution System (MES) Simulation"