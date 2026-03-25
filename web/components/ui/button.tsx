import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-xl border text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "border-cyan-400/30 bg-cyan-300/10 px-4 py-2.5 text-cyan-100 hover:bg-cyan-300/15",
        secondary: "border-white/10 bg-white/5 px-4 py-2.5 text-slate-100 hover:bg-white/10",
        ghost: "border-transparent bg-transparent px-3 py-2 text-slate-300 hover:bg-white/5",
      },
      size: {
        default: "h-11",
        sm: "h-9 px-3 text-xs",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({ className, variant, size, ...props }, ref) => (
  <button ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />
));

Button.displayName = "Button";

export { Button, buttonVariants };
