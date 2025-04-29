import mongoose from 'mongoose';
import config from './config';

export async function connectToDatabase() {
  try {
    await mongoose.connect(config.mongodb.uri);
    console.log("Connected to database!");
  } catch (error) {
    console.error("Connection failed:", error);
    process.exit(1);
  }
} 