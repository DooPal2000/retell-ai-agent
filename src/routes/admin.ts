import express from 'express';
import passport from 'passport';
import { Router } from 'express';

import catchAsync from '../utils/catchAsync';
import { isLoggedIn, isSecureAdminCreation, isAdmin } from '../middleware';
import * as admin from '../controllers/Cadmin';

const router: Router = express.Router();

router.get('/', isAdmin, catchAsync(admin.renderAdmin));

router.patch('/toggle-active/:userId', isAdmin, catchAsync(admin.toggleUserActive));

router.delete('/delete-user/:userId', isAdmin, catchAsync(admin.deleteUser));

export default router; 