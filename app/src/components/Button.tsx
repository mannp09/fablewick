import type { AnchorHTMLAttributes, ButtonHTMLAttributes, ReactNode } from 'react';
import { Link, type LinkProps as RouterLinkProps } from 'react-router-dom';
import './Button.css';

type Variant = 'filled' | 'outline' | 'ghost';

interface BaseProps {
  variant?: Variant;
  children: ReactNode;
}

type AnchorProps = BaseProps &
  AnchorHTMLAttributes<HTMLAnchorElement> & { href: string; to?: undefined };
type RouteProps = BaseProps & RouterLinkProps & { to: string; href?: undefined };
type ButtonProps = BaseProps &
  ButtonHTMLAttributes<HTMLButtonElement> & { href?: undefined; to?: undefined };

// One button for the whole app: filled (primary), outline (secondary) or
// ghost (quiet, text-weight). 44px minimum height everywhere per the
// design system's tap-target floor. Renders a react-router Link for an
// in-app route (`to`), a plain anchor for an external/asset href
// (`href`), or a <button> for an action with neither.
export default function Button(props: AnchorProps | RouteProps | ButtonProps) {
  const { variant = 'filled', children, className, ...rest } = props;
  const cls = ['btn', `btn-${variant}`, className].filter(Boolean).join(' ');

  if ('to' in rest && rest.to !== undefined) {
    const { to, ...linkRest } = rest as Omit<RouteProps, 'variant' | 'children' | 'className'>;
    return (
      <Link className={cls} to={to} {...linkRest}>
        {children}
      </Link>
    );
  }

  if ('href' in rest && rest.href) {
    const anchorRest = rest as AnchorHTMLAttributes<HTMLAnchorElement>;
    const isExternal = /^https?:\/\//.test(anchorRest.href ?? '');
    const externalProps = isExternal ? { target: '_blank', rel: 'noopener' } : {};
    return (
      <a className={cls} {...externalProps} {...anchorRest}>
        {children}
      </a>
    );
  }

  return (
    <button className={cls} {...(rest as ButtonHTMLAttributes<HTMLButtonElement>)}>
      {children}
    </button>
  );
}
