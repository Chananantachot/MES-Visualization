Feature: Motor speed
    Scenario: Check if Motor speed route works
        Given the Mes motor speed is running
        When I request the "/ai/motorSpeed" endpoint
        Then I should receive "Motor Speed vs Temperature (AI Analysis)"

    Scenario: Check if Motor speed api route works
        Given the Mes motor speed is running
        When I request the "/ai/motorSpeed" api endpoint
        Then I should receive json data back    