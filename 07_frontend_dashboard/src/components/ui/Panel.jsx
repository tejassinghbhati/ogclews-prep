import React from 'react';

export function Panel({ title, actions, children, glow, className = '', style = {} }) {
  return (
    <div
      className={`panel ${glow ? `panel--glow-${glow}` : ''} ${className}`}
      style={style}
    >
      {title && (
        <div className="panel__header">
          <span className="panel__title">{title}</span>
          {actions && <div className="panel__actions">{actions}</div>}
        </div>
      )}
      <div className="panel__body">{children}</div>
    </div>
  );
}
