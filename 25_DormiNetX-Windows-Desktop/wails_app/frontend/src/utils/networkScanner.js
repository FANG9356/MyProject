
export const scanSubnetForServer = async (subnet) => {
  const promises = [];
  
  for (let i = 1; i <= 254; i++) {
    const ip = `${subnet}.${i}`;
    const testUrl = `http://${ip}:4282/api/system/ping`;
    
    const p = new Promise((resolve) => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
        resolve(null);
      }, 1500); 

      fetch(testUrl, { 
        method: 'GET', 
        signal: controller.signal 
      })
      .then(res => {
        clearTimeout(timeoutId);
        
        if (res.ok || res.status === 401) {
          resolve(ip);
        } else {
          resolve(null);
        }
      })
      .catch(() => {
        clearTimeout(timeoutId);
        resolve(null);
      });
    });

    promises.push(p);
  }

  const results = await Promise.all(promises);
  
  return results.find(ip => ip !== null);
};

export const autoDiscoverServer = async () => {
  let subnetsToScan = [];

  if (window.go && window.go.main && window.go.main.App && window.go.main.App.GetLocalSubnet) {
    try {
      const exactSubnet = await window.go.main.App.GetLocalSubnet();
      if (exactSubnet) {
        subnetsToScan.push(exactSubnet);
      }
    } catch (err) {
      console.error("Failed to get subnet from Go:", err);
    }
  }

  const hostname = window.location.hostname;
  if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
    const parts = hostname.split('.');
    if (parts.length === 4) {
      const browserSubnet = `${parts[0]}.${parts[1]}.${parts[2]}`;
      if (!subnetsToScan.includes(browserSubnet)) {
        subnetsToScan.push(browserSubnet);
      }
    }
  }

  if (subnetsToScan.length === 0) {
    subnetsToScan = ['192.168.1', '192.168.0', '10.0.0'];
  }

  for (const subnet of subnetsToScan) {
    console.log(`Scanning subnet ${subnet}.* for DormiNet Server...`);
    const foundIp = await scanSubnetForServer(subnet);
    if (foundIp) {
      console.log(`Server found at: ${foundIp}`);
      return foundIp;
    }
  }

  return null;
};
