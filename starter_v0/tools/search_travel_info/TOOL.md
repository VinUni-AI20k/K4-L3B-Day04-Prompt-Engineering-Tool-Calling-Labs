# search_travel_info
Searches the public web for current travel information using the Tavily Search API.

## Use cases
Use this tool for up-to-date public travel information such as:

- Tourist attractions
- Restaurants and local food
- Hotels and accommodation
- Transportation
- Events and festivals
- General destination information

## Arguments
- `query`: Search request.
- `destination`: City, region, or country.
- `category`: `general`, `attraction`, `food`, `hotel`, `transport`, or `event`.
- `max_results`: Number of results to return (1-10).

## Safety
This tool sends the search query to an external web search service.

Never include:
- Passwords
- API keys or tokens
- Payment information
- Private identifiers
- Sensitive personal information
- Internal or confidential data

## Output
Returns structured web search evidence including:

- Title
- URL
- Content snippet
- Relevance score
- Search metadata