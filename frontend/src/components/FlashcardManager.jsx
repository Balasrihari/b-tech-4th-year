import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { flashcardsService } from '../services/flashcards';
import { Plus, BookOpen, RotateCcw, Trash2, Edit2, Layers } from 'lucide-react';

export default function FlashcardManager() {
  const [showForm, setShowForm] = useState(false);
  const [reviewMode, setReviewMode] = useState(false);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [formData, setFormData] = useState({ front: '', back: '', deck_name: 'Default' });
  const [selectedDeck, setSelectedDeck] = useState(null);
  const queryClient = useQueryClient();

  const { data: flashcards, isLoading } = useQuery({
    queryKey: ['flashcards', selectedDeck],
    queryFn: () => flashcardsService.getAll(selectedDeck),
  });

  const { data: decks } = useQuery({
    queryKey: ['flashcardDecks'],
    queryFn: flashcardsService.getDecks,
  });

  const { data: reviewCards } = useQuery({
    queryKey: ['flashcardsForReview', selectedDeck],
    queryFn: () => flashcardsService.getForReview(selectedDeck),
    enabled: reviewMode,
  });

  const createMutation = useMutation({
    mutationFn: flashcardsService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['flashcards']);
      queryClient.invalidateQueries(['flashcardDecks']);
      setShowForm(false);
      setFormData({ front: '', back: '', deck_name: 'Default' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: flashcardsService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['flashcards']);
    },
  });

  const reviewMutation = useMutation({
    mutationFn: flashcardsService.submitReview,
    onSuccess: () => {
      queryClient.invalidateQueries(['flashcardsForReview']);
      setShowAnswer(false);
      if (currentCardIndex < (reviewCards?.length || 0) - 1) {
        setCurrentCardIndex(currentCardIndex + 1);
      } else {
        setReviewMode(false);
        setCurrentCardIndex(0);
      }
    },
  });

  const handleCreate = (e) => {
    e.preventDefault();
    if (formData.front.trim() && formData.back.trim()) {
      createMutation.mutate(formData);
    }
  };

  const handleReviewRating = (rating) => {
    if (reviewCards && reviewCards[currentCardIndex]) {
      reviewMutation.mutate({
        flashcard_id: reviewCards[currentCardIndex].id,
        rating: rating
      });
    }
  };

  if (isLoading) return <div>Loading flashcards...</div>;

  if (reviewMode && reviewCards && reviewCards.length > 0) {
    const card = reviewCards[currentCardIndex];
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Review Mode</h2>
          <button
            onClick={() => setReviewMode(false)}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            Exit Review
          </button>
        </div>
        <div className="text-center mb-4 text-gray-600 dark:text-gray-400">
          Card {currentCardIndex + 1} of {reviewCards.length}
        </div>
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-700 dark:to-gray-600 rounded-lg p-8 min-h-[300px] flex flex-col justify-center items-center">
          <p className="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            {card.front}
          </p>
          {showAnswer ? (
            <p className="text-xl text-gray-700 dark:text-gray-300">
              {card.back}
            </p>
          ) : (
            <button
              onClick={() => setShowAnswer(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Show Answer
            </button>
          )}
        </div>
        {showAnswer && (
          <div className="mt-6 flex justify-center gap-4">
            <button
              onClick={() => handleReviewRating(1)}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
            >
              Again (1)
            </button>
            <button
              onClick={() => handleReviewRating(3)}
              className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600"
            >
              Good (3)
            </button>
            <button
              onClick={() => handleReviewRating(5)}
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
            >
              Easy (5)
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Flashcards</h2>
        <div className="flex gap-2">
          <button
            onClick={() => {
              const dueCards = flashcards?.filter(f => f.status === 'new' || f.status === 'learning').length || 0;
              if (dueCards > 0) setReviewMode(true);
            }}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
            disabled={!flashcards?.length}
          >
            <RotateCcw size={20} />
            Review ({flashcards?.filter(f => f.status === 'new' || f.status === 'learning').length || 0} due)
          </button>
          <button
            onClick={() => { setShowForm(true); setFormData({ front: '', back: '', deck_name: selectedDeck || 'Default' }); }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <Plus size={20} />
            Add Card
          </button>
        </div>
      </div>

      <div className="mb-6 flex gap-2 items-center">
        <Layers size={20} className="text-gray-600 dark:text-gray-400" />
        <select
          value={selectedDeck || 'all'}
          onChange={(e) => setSelectedDeck(e.target.value === 'all' ? null : e.target.value)}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
        >
          <option value="all">All Decks</option>
          {decks?.decks?.map((deck) => (
            <option key={deck} value={deck}>{deck}</option>
          ))}
        </select>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="mb-6 p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">New Flashcard</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Front (Question)</label>
              <textarea
                value={formData.front}
                onChange={(e) => setFormData({ ...formData, front: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                rows="2"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Back (Answer)</label>
              <textarea
                value={formData.back}
                onChange={(e) => setFormData({ ...formData, back: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                rows="2"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Deck Name</label>
              <input
                type="text"
                value={formData.deck_name}
                onChange={(e) => setFormData({ ...formData, deck_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                required
              />
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Create
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                Cancel
              </button>
            </div>
          </div>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {flashcards?.map((card) => (
          <div key={card.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-2">
              <BookOpen className="text-blue-600 dark:text-blue-400" size={20} />
              <span className="text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
                {card.deck_name}
              </span>
            </div>
            <p className="font-semibold text-gray-900 dark:text-white mb-2">{card.front}</p>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{card.back}</p>
            <div className="flex items-center justify-between">
              <span className={`text-xs px-2 py-1 rounded ${
                card.status === 'mastered' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                card.status === 'review' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
              }`}>
                {card.status}
              </span>
              <button
                onClick={() => deleteMutation.mutate(card.id)}
                className="p-1 text-gray-600 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
