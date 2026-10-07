// Netlify Function: proxies /api/countries to REST Countries.
// Set the environment variable RESTCOUNTRIES_KEY in Netlify
// (Site configuration -> Environment variables).
exports.handler = async (event) => {
  const qs = new URLSearchParams(event.queryStringParameters || {}).toString();
  const res = await fetch(
    "https://api.restcountries.com/countries/v5" + (qs ? "?" + qs : ""),
    {
      headers: {
        Authorization: "Bearer " + process.env.RESTCOUNTRIES_KEY,
        Accept: "application/json",
        "User-Agent": "WorldCountriesApp/1.0",
      },
    }
  );
  return {
    statusCode: res.status,
    headers: { "Content-Type": "application/json" },
    body: await res.text(),
  };
};
