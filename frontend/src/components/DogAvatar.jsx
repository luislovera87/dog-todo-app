export const getDogEmoji = (dogName) => {
  const emojis = {
    buddy: '🐕',
    max: '🐶',
    luna: '🐕',
    bella: '🐕‍🦺',
    charlie: '🦴',
  }
  return emojis[dogName?.toLowerCase()] || '🐾'
}

export default function DogAvatar({ dogName }) {
  return (
    <span className="dog-avatar">
      {getDogEmoji(dogName)}
    </span>
  )
}
