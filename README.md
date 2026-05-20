# Delivery-Service-Insights

## Insights are based off delivery service on bicycle within a city

### Data for this project is acquired from Doordash's dasher app and Uber's delivery app
#### Data in consideration:
1. Total Earnings per Day
2. Earnings per order
3. Active service time (on delivery)
4. total service time per Day
5. Distance traveled per order
6. Total Distance traveled per day

#### Future Considerations:
1. Route taken in city
2. traffic heat per order
3. traffic heat per session (average)
4. route rating (scoring - ML)

#### Questions to consider:
- How do store data while collecting it
- Which apps like Gridwise or Stride should be used for tracking metrics

- 
- REAL data accumulated
- SIMULATED data 

#### Appplications
- Strava Rest API
- Door Dash / Uber Delivery export

  ##### Process

  - Accumulate data from food delivery
  - Record on Strava and export to JSON
  - either work JSON or convert to csv/dataframe
  - One month of data can be simulated (upon completion of data collection

  ##### Delivery Data
  - Will be processed by session (case by case)
  - earned by day (SUM of session from 4am-3:59am
  - session has X hours
  - rate: earned by day / total hours in day
