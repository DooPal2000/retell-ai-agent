// import { Request, Response, NextFunction } from 'express';
// import User from '../models/user_bk20250427';
// import ExpressError from '../utils/ExpressError';

// export const renderAdmin = async (req: Request, res: Response) => {
//     const users = await User.find({ role: 'user' }).select('-password');
//     res.render('admin/admin', { users: users });
// };

// export const toggleUserActive = async (req: Request, res: Response) => {
//     const { userId } = req.params;
//     const { isActive } = req.body;

//     const user = await User.findById(userId);
//     console.log('Before update:', user.isActive);

//     user.isActive = !user.isActive;
//     await user.save();

//     console.log('After update:', user.isActive);

//     const updatedUser = await User.findById(userId);
//     console.log('Final state:', updatedUser.isActive);

//     res.json({ success: true, isActive: user.isActive });
// };

// export const deleteUser = async (req: Request, res: Response) => {
//     const { userId } = req.params;
//     await User.findByIdAndDelete(userId);
//     res.json({ success: true });
// }; 