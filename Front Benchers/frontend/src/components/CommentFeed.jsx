import { useRef, useEffect } from 'react';
import './CommentFeed.css';

const CommentFeed = ({ comments }) => {
  const feedRef = useRef(null);

  // Auto-scroll to bottom when new comments arrive
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [comments]);

  if (comments.length === 0) {
    return (
      <div className="comment-feed" id="comment-feed">
        <div className="comment-feed-inner" ref={feedRef}>
          <div className="comment-empty">
            <span className="empty-icon">💬</span>
            <p>Start coding and your coach will react to your approach...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="comment-feed" id="comment-feed">
      <div className="comment-feed-inner" ref={feedRef}>
        {comments.map((comment, i) => (
          <div
            key={comment.timestamp + i}
            className={`comment-line comment-tone-${comment.tone}`}
          >
            <span className="comment-prompt">&gt;</span>
            <span className="comment-text">{comment.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CommentFeed;
