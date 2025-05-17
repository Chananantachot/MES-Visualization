Feature: Production Rate Rest API
    Scenario: Check if Production Rate Rest API route works
        Given the Mes opcua server is running
        When I request the "/opcua/products" endpoint
        Then I should receive graph data