import os
from gql import gql

from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from decimal import Decimal


class SubgraphClient:
    def __init__(self, url: str = None) -> None:
        transport = AIOHTTPTransport(url=url)
        self.client = Client(transport=transport,
                             fetch_schema_from_transport=True)

    async def get_pairs(self):
        query = gql(
            """
          query getPairs {
              pairs(first: 1000) {
                id
                from
                to
                feed
              }
            }
      """
        )

        # Execute the query on the transport
        result = await self.client.execute_async(query)

        return result['pairs']

    async def get_pair_details(self, pair_id):
        query = gql(
            """
          query getPairDetails($pair_id: ID!){
            pair(id: $pair_id) {
              id
              from
              to                    
              longOI
              shortOI
              maxOI
              makerFeeP
              takerFeeP
              usageFeeP
              utilizationThresholdP
              makerMaxLeverage    
              curFundingLong  
              curFundingShort
              curRollover
              maxLeverage
              accRollover
              lastRolloverBlock
              rolloverFeePerBlock
              accFundingLong
              accFundingShort
              lastFundingBlock
              maxFundingFeePerBlock
              lastFundingVelocity
              lastFundingRate
              group {
                id
                name
                minLeverage
                maxLeverage
                maxCollateralP
                longCollateral
                shortCollateral
              }
              fee {
                minLevPos                
              }
          }
          }
          """
        )
        result = await self.client.execute_async(query, variable_values={"pair_id": str(pair_id)})

        # Convert Decimal fields to float or str
        if result and 'pair' in result:
            pair = result['pair']
            for key, value in pair.items():
                if isinstance(value, Decimal):
                    pair[key] = float(value)  # or str(value) if you prefer
            return pair
        else:
            raise ValueError(f"No pair details found for pair ID: {pair_id}")

    async def get_open_trades(self, trader):
        query = gql(
            """
          query trades($trader: Bytes!) {
        trades(        
          where: { isOpen: true, trader: $trader }
        ) {
          tradeID
          collateral
          leverage
          openPrice
          stopLossPrice
          takeProfitPrice
          isOpen
          timestamp
          isBuy
          notional
          tradeNotional
          funding
          rollover
          trader
          index
          pair {
            id
            feed
            from
            to
            accRollover
            lastRolloverBlock
            rolloverFeePerBlock
            accFundingLong
            spreadP
            tradeSizeRef
            accFundingShort
            longOI
            shortOI
            lastFundingBlock
            maxFundingFeePerBlock
            lastFundingVelocity
            lastFundingRate
          }
        }
      }
          """
        )
        result = await self.client.execute_async(query, variable_values={"trader": trader})

        # print(result)

        return result['trades']

    async def get_orders(self, trader):
        query = gql(
            """
          query orders($trader: Bytes!) {
            limits(
              where: { trader: $trader, isActive: true }
              orderBy: initiatedAt
              orderDirection: asc
            ) {
              collateral
              leverage
              isBuy
              isActive
              id
              openPrice
              takeProfitPrice
              stopLossPrice
              trader
              initiatedAt
              limitType
              pair {
                id
                feed
                from
                to
                accRollover
                lastRolloverBlock
                rolloverFeePerBlock
                accFundingLong
                spreadP
                tradeSizeRef
                accFundingShort
                longOI
                shortOI
                lastFundingBlock
                maxFundingFeePerBlock
                lastFundingVelocity
                lastFundingRate
              }
            }
          }
          """
        )
        result = await self.client.execute_async(query, variable_values={"trader": trader})

        return result['limits']
