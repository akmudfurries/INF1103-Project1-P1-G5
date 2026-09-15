1. Problem Statement and Target Users

Application:
AI Inventory & Procurement Advisor

Problem Statement:
Businesses need to maintain enough inventory to meet customer demand while avoiding unnecessary stock and procurement costs. However, deciding when and how much to reorder can be difficult, especially when demand changes over time. Over ordering can lead to excess inventory and increased storage costs, while under ordering can result in stockouts, delayed orders and lost sales.
The AI Inventory & Procurement Advisor aims to address this problem by combining structured inventory data with unstructured operational information. The AI will interpret operational notes to identify factors such as changing demand, supplier issues and operational importance. These AI-generated insights will then be evaluated by predefined business rules in python to produce a procurement recommendation.

Intended Users:
Small business owners
Inventory management staff
Procurement management staff
Retail businesses
2. User Inputs


User will enter inventory records, that include:


Item Name: Industrial Printer Ribbon
Category of Item: Printing Supplies
Current Stock of Item: 42 units
Average Weekly Usage: 15 units
Minimum Order Quantity: 50 units
Unit Cost: $12
Available Budget: $500
Operational Notes: “Usage has increased significantly since the new warehouse opened and our supplier has been late with the last two orders.” 

The system will calculate relevant numerical values, such as average usage and stock coverage, from the provided data. The operational notes will be passed to the AI for interpretation.

3. Core concept


AI interprets the unstructured operational context
Python makes the procurement recommendation
JSON stores the result

3.1 Use of AI
Every inventory record requiring an assessment will be sent through the AI API. The AI will interpret the operational context and return structured JSON. The AI will be responsible for interpreting the unstructured operational context, rather than making the final procurement decision. 

The AI may identify:
Demand Level: Low / Medium / High
Demand Trend: Decreasing / Stable / Increasing
Supplier Issue: None / Potential / Significant
Operational Importance: Low / Medium / High

The AI will not directly make the final procurement decision. Its response will first be to checked against a predefined schema to ensure: 

Required fields exist 
Data types are correct 
Values belong to accepted categories 

Invalid or malformed responses are rejected after successful validation, the structured AI insights will be passed to the deterministic Python business rules.

4. Business Rules 

After successful AI validation, Python will apply deterministic procurement rules. Possible rules include:

Stock Coverage: Calculate how many weeks the current stock can support
Reorder Point: Compares current stock to recommended stocks to have
Recommended Order Quantity: Give recommended quantity of items to order
Procurement Priority: Level of importance of the stock based on risk, cost and demand trend

The final procurement decision is determined by Python business rules rather than directly by the AI itself.
 
GitHub Repository Link: https://github.com/akmudfurries/INF1103-Group-5-Project 
