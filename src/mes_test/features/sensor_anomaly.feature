Feature: Analyze Sensor Anomaly

  Scenario: Generate sensor anomaly table and summary
    Given the sensor anomaly function is executed
    Then the sensor anomaly output should include an HTML table
    And the sensor_summary should contain Anomaly Flag
