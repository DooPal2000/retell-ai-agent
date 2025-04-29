// import { Request, Response, NextFunction } from 'express';
// import Product from '../models/product';
// import User from '../models/user_bk20250427';
// import ExpressError from '../utils/ExpressError';

// export const index = async (req: Request, res: Response) => {
//     const products = await Product.find({ createdBy: req.user!._id });
//     res.render('products/index', { products });
// };

// export const renderNewForm = (req: Request, res: Response) => {
//     res.render('products/new');
// };

// export const createProduct = async (req: Request, res: Response) => {
//     const product = new Product(req.body.product);
//     product.createdBy = req.user!._id;
//     await product.save();

//     res.redirect('/products');
// };

// export const showProduct = async (req: Request, res: Response) => {
//     const product = await Product.findById(req.params.id);
//     res.render('products/edit', { product });
// };

// export const renderEditForm = async (req: Request, res: Response) => {
//     const product = await Product.findById(req.params.id);
//     res.render('products/edit', { product });
// };

// export const updateProduct = async (req: Request, res: Response) => {
//     const { id } = req.params;
//     const product = await Product.findByIdAndUpdate(id, { ...req.body.product });

//     const products = await Product.find({ createdBy: req.user!._id });

//     res.redirect('/products');
// };

// export const updateQuantity = async (req: Request, res: Response, next: NextFunction) => {
//     const { id } = req.params;
//     const { quantity } = req.body;

//     if (typeof quantity !== 'number' || quantity < 0 || !Number.isInteger(quantity)) {
//         throw new ExpressError('수량은 0 이상의 정수여야 합니다.', 400);
//     }

//     const product = await Product.findById(id);
//     if (!product) {
//         throw new ExpressError('상품을 찾을 수 없습니다.', 404);
//     }

//     product.quantity = quantity;
//     await product.save();

//     res.json({ success: true, quantity: product.quantity });
// };

// export const deleteProduct = async (req: Request, res: Response) => {
//     const { id } = req.params;
//     await Product.findByIdAndDelete(id);
//     res.redirect('/products');
// }; 