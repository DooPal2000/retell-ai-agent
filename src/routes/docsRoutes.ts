import express from 'express';
import passport from 'passport';
import { Router } from 'express';

import catchAsync from '../utils/catchAsync';
// import { isLoggedIn, isSecureAdminCreation, isAuthorized, isRealPhone } from '../middleware';
import * as users from '../controllers/Cusers';

const router: Router = express.Router();

router.get('/register', users.renderRegister);
router.get('/register/admin', users.renderRegisterAdmin);

router.post('/register', catchAsync(users.register));
router.post('/register/admin', catchAsync(users.registerAdmin));

router.get('/login', users.renderLogin);

router.post('/login', users.login);

router.get('/logout', users.logout);

export default router; 