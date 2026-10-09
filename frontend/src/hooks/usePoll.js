import { useEffect, useState } from "react";
import api from "../api/client.js";

export default function usePoll(url, ms = 3000) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  useEffect(() => {
    let on = true;
    const load = () =>
      api.get(url).then((r) => on && (setData(r.data), setError(null))).catch((e) => on && setError(e));
    load();
    const t = setInterval(load, ms);
    return () => { on = false; clearInterval(t); };
  }, [url, ms]);
  return { data, error };
}
