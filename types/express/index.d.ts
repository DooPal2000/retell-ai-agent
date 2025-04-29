// src/types/express/index.d.ts
import { IUser } from '../../src/models/user';

declare global {
  namespace Express {
   interface User extends IUser {}
  }
}
