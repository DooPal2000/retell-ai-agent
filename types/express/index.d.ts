// src/types/express/index.d.ts
import { IUser } from '../../models/user';

declare global {
  namespace Express {
    interface User extends IUser {}
  }
}
