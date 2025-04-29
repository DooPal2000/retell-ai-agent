import fs from 'fs';
import dotenv from 'dotenv';

interface Config {
  mongodb: {
    uri: string;
  };
  admin: {
    numbers: Record<string, any>;
  };
  session: {
    secretKey: string;
  };
}

function loadEnvironment() {
  if (process.env.NODE_ENV === 'production') {
    return process.env;
  } else {
    dotenv.config({ path: './.env' });
    return process.env;
  }
}

const env = loadEnvironment();

const config: Config = {
  mongodb: {
    uri: env.MONGODB_URI || ''
  },
  admin: {
    numbers: JSON.parse(env.ADMIN_NUMBERS || '{}')
  },
  session: {
    secretKey: env.SESSION_SECRET_KEY || ''
  }
};

export default config; 