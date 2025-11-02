const apiToken = process.env.NEXT_PUBLIC_API_ACCESS_TOKEN;
// export const API_URL = "https://api.thebluetonguegiraffe.online";
export const API_URL = "http://localhost:7000"
export const DEFAULT_HEADERS = {
  "Content-Type": "application/json",
  "Authorization": `Bearer ${apiToken}`
};