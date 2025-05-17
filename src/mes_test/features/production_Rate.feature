Feature: Production Rate Rest API
    Scenario: Check if Production Rate Rest API route works
        Given the Mes opcua server is running
        When I request the "/opcua/products" endpoint
        Then I should receive graph data

    Scenario: Check if Production Rate route works
        Given the Mes opcua server is running
        When I request the "/productionRates" endpoint
        Then I should receive "Visualization of MES Production Rate Simulation"