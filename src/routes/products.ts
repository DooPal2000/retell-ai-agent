// import express from 'express';
// import passport from 'passport';
// import { Router } from 'express';

// import catchAsync from '../utils/catchAsync';
// import { isLoggedIn, isSecureAdminCreation, isAuthorized } from '../middleware';
// import products from '../controllers/Cproduct';

// const router: Router = express.Router();

// router.route('/')
//     .get(isAuthorized, catchAsync(products.index))
//     .post(isAuthorized, catchAsync(products.createProduct));

// router.get('/new', isAuthorized, products.renderNewForm);

// router.route('/:id')
//     .get(isAuthorized, catchAsync(products.showProduct))
//     .put(isAuthorized, catchAsync(products.updateProduct))
//     .delete(isAuthorized, catchAsync(products.deleteProduct));

// router.get('/:id/edit', isAuthorized, catchAsync(products.renderEditForm));

// router.post('/:id/update-quantity', isAuthorized, catchAsync(products.updateQuantity));

// export default router; 