// Netlify Function: proxies /api/countries to REST Countries.
// Needs the environment variable RESTCOUNTRIES_KEY (then redeploy).
exports.handler = async (event) => {
  // Strip stray spaces / quotes / line breaks that sneak into env vars
  const key = (process.env.RESTCOUNTRIES_KEY || "").trim().replace(/^["']|["']$/g, "").trim();

  if (!key) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        errors: [{ message: "RESTCOUNTRIES_KEY is not set on this Netlify site. Add it under Site configuration > Environment variables, then redeploy." }],
      }),
    };
  }

  const qs = new URLSearchParams(event.queryStringParameters || {}).toString();
  const res = await fetch(
    "https://api.restcountries.com/countries/v5" + (qs ? "?" + qs : ""),
    {
      headers: {
        Authorization: "Bearer " + key,
        Accept: "application/json",
        "User-Agent": "WorldCountriesApp/1.0",
      },
    }
  );
  console.log("REST Countries answered", res.status, "key length", key.length);
  return {
    statusCode: res.status,
    headers: { "Content-Type": "application/json" },
    body: await res.text(),
  };
};
