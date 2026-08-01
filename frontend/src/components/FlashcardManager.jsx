import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { flashcardsService } from '../services/flashcards';
import { Plus, BookOpen, RotateCcw, Trash2, Edit2, Layers, Calendar, TrendingUp, BarChart3, ArrowLeft, Upload } from 'lucide-react';

export default function FlashcardManager() {
  const [showForm, setShowForm] = useState(false);
  const [reviewMode, setReviewMode] = useState(false);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [formData, setFormData] = useState({ front: '', back: '', deck_name: 'Default' });
  const [selectedDeck, setSelectedDeck] = useState(null);
  const [flashcardMode, setFlashcardMode] = useState('list'); // list, review, statistics, progress, schedule
  const [batchFormData, setBatchFormData] = useState([{ front: '', back: '', deck_name: 'Default' }]);
  const queryClient = useQueryClient();

  const { data: flashcards, isLoading, error } = useQuery({
    queryKey: ['flashcards', selectedDeck],
    queryFn: () => flashcardsService.getAll(selectedDeck),
    enabled: flashcardMode === 'list',
  });

  const { data: decks } = useQuery({
    queryKey: ['flashcardDecks'],
    queryFn: flashcardsService.getDecks,
  });

  const { data: reviewCards } = useQuery({
    queryKey: ['flashcardsForReview', selectedDeck],
    queryFn: () => flashcardsService.getForReview(selectedDeck),
    enabled: flashcardMode === 'review',
  });

  const { data: deckStatistics } = useQuery({
    queryKey: ['deckStatistics'],
    queryFn: flashcardsService.getDeckStatistics,
    enabled: flashcardMode === 'statistics',
  });

  const { data: flashcardProgress } = useQuery({
    queryKey: ['flashcardProgress'],
    queryFn: () => flashcardsService.getProgress({ days: 30 }),
    enabled: flashcardMode === 'progress',
  });

  const { data: studySchedule } = useQuery({
    queryKey: ['studySchedule'],
    queryFn: () => flashcardsService.getStudySchedule({ days: 7 }),
    enabled: flashcardMode === 'schedule',
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

  const batchCreateMutation = useMutation({
    mutationFn: flashcardsService.createBatch,
    onSuccess: () => {
      queryClient.invalidateQueries(['flashcards']);
      queryClient.invalidateQueries(['flashcardDecks']);
      setBatchFormData([{ front: '', back: '', deck_name: 'Default' }]);
      setFlashcardMode('list');
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

  const handleBatchCreate = (e) => {
    e.preventDefault();
    const validCards = batchFormData.filter(card => card.front.trim() && card.back.trim());
    if (validCards.length > 0) {
      batchCreateMutation.mutate(validCards);
    }
  };

  const handleAddBatchCard = () => {
    setBatchFormData([...batchFormData, { front: '', back: '', deck_name: batchFormData[0].deck_name || 'Default' }]);
  };

  const handleRemoveBatchCard = (index) => {
    setBatchFormData(batchFormData.filter((_, i) => i !== index));
  };

  const handleReviewRating = (rating) => {
    if (reviewCards && reviewCards[currentCardIndex]) {
      reviewMutation.mutate({
        flashcard_id: reviewCards[currentCardIndex].id,
        rating: rating
      });
    }
  };

  if (isLoading && flashcardMode === 'list') {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600 dark:text-gray-400">Loading flashcards...</span>
        </div>
      </div>
    );
  }

  if (error && flashcardMode === 'list') {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="text-red-600 dark:text-red-400 text-center py-12">
          <p>Error loading flashcards: {error.message}</p>
          <button onClick={() => queryClient.invalidateQueries(['flashcards'])} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (flashcardMode === 'list') {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex flex-wrap justify-between items-center mb-6 gap-4">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Flashcards</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setFlashcardMode('statistics')}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
            >
              <BarChart3 size={16} />
              Statistics
            </button>
            <button
              onClick={() => setFlashcardMode('progress')}
              className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 flex items-center gap-2"
            >
              <TrendingUp size={16} />
              Progress
            </button>
            <button
              onClick={() => setFlashcardMode('schedule')}
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 flex items-center gap-2"
            >
              <Calendar size={16} />
              Schedule
            </button>
            <button
              onClick={() => setFlashcardMode('batch')}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
            >
              <Upload size={16} />
              Batch Import
            </button>
            <button
              onClick={() => {
                const dueCards = flashcards?.filter(f => f.status === 'new' || f.status === 'learning').length || 0;
                if (dueCards > 0) { setFlashcardMode('review'); setReviewMode(true); }
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
                  disabled={createMutation.isLoading}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  {createMutation.isLoading ? 'Creating...' : 'Create'}
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

        {!flashcards || flashcards.length === 0 ? (
          <div className="text-center py-12 text-gray-600 dark:text-gray-400">
            <p>No flashcards yet. Add your first card to get started!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {flashcards.map((card) => (
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
        )}
      </div>
    );
  }

  if (flashcardMode === 'batch') {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-6">
          <button onClick={() => setFlashcardMode('list')} className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
            <ArrowLeft size={20} />
          </button>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Batch Import Flashcards</h2>
        </div>

        <form onSubmit={handleBatchCreate} className="space-y-4">
          {batchFormData.map((card, index) => (
            <div key={index} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="font-semibold text-gray-900 dark:text-white">Card {index + 1}</span>
                {batchFormData.length > 1 && (
                  <button
                    type="button"
                    onClick={() => handleRemoveBatchCard(index)}
                    className="text-red-600 dark:text-red-400 hover:text-red-700"
                  >
                    <Trash2 size={16} />
                  </button>
                )}
              </div>
              <div className="space-y-2">
                <input
                  type="text"
                  value={card.front}
                  onChange={(e) => {
                    const newCards = [...batchFormData];
                    newCards[index].front = e.target.value;
                    setBatchFormData(newCards);
                  }}
                  placeholder="Front (Question)"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
                <input
                  type="text"
                  value={card.back}
                  onChange={(e) => {
                    const newCards = [...batchFormData];
                    newCards[index].back = e.target.value;
                    setBatchFormData(newCards);
                  }}
                  placeholder="Back (Answer)"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
                <input
                  type="text"
                  value={card.deck_name}
                  onChange={(e) => {
                    const newCards = [...batchFormData];
                    newCards[index].deck_name = e.target.value;
                    setBatchFormData(newCards);
                  }}
                  placeholder="Deck Name"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>
          ))}

          <button
            type="button"
            onClick={handleAddBatchCard}
            className="w-full px-4 py-2 border-2 border-dashed border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 rounded-lg hover:border-blue-500 hover:text-blue-500"
          >
            + Add Another Card
          </button>

          <div className="flex gap-2">
            <button
              type="submit"
              disabled={batchCreateMutation.isLoading}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {batchCreateMutation.isLoading ? 'Importing...' : 'Import All Cards'}
            </button>
            <button
              type="button"
              onClick={() => setFlashcardMode('list')}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    );
  }

  if (flashcardMode === 'statistics') {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-6">
          <button onClick={() => setFlashcardMode('list')} className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
            <ArrowLeft size={20} />
          </button>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Deck Statistics</h2>
        </div>

        {deckStatistics ? (
          <div className="space-y-4">
            {deckStatistics.length === 0 ? (
              <p className="text-gray-600 dark:text-gray-400 text-center py-8">No decks found</p>
            ) : (
              deckStatistics.map((deck) => (
                <div key={deck.deck_name} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-3">{deck.deck_name}</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                      <p className="text-sm text-gray-600 dark:text-gray-400">Total</p>
                      <p className="text-xl font-bold text-gray-900 dark:text-white">{deck.total_cards}</p>
                    </div>
                    <div className="bg-blue-50 dark:bg-blue-900 rounded-lg p-3">
                      <p className="text-sm text-blue-600 dark:text-blue-400">New</p>
                      <p className="text-xl font-bold text-blue-900 dark:text-blue-200">{deck.new_cards}</p>
                    </div>
                    <div className="bg-yellow-50 dark:bg-yellow-900 rounded-lg p-3">
                      <p className="text-sm text-yellow-600 dark:text-yellow-400">Learning</p>
                      <p className="text-xl font-bold text-yellow-900 dark:text-yellow-200">{deck.learning_cards}</p>
                    </div>
                    <div className="bg-green-50 dark:bg-green-900 rounded-lg p-3">
                      <p className="text-sm text-green-600 dark:text-green-400">Mastered</p>
                      <p className="text-xl font-bold text-green-900 dark:text-green-200">{deck.mastered_cards}</p>
                    </div>
                  </div>
                  <div className="mt-3 text-sm text-gray-600 dark:text-gray-400">
                    Due for review: <span className="font-semibold text-orange-600 dark:text-orange-400">{deck.due_for_review}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        ) : (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        )}
      </div>
    );
  }

  if (flashcardMode === 'progress') {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-6">
          <button onClick={() => setFlashcardMode('list')} className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
            <ArrowLeft size={20} />
          </button>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Learning Progress</h2>
        </div>

        {flashcardProgress ? (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Cards</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{flashcardProgress.total_cards}</p>
              </div>
              <div className="bg-green-50 dark:bg-green-900 rounded-lg p-4">
                <p className="text-sm text-green-600 dark:text-green-400">Mastered</p>
                <p className="text-2xl font-bold text-green-900 dark:text-green-200">{flashcardProgress.mastered_cards}</p>
              </div>
              <div className="bg-blue-50 dark:bg-blue-900 rounded-lg p-4">
                <p className="text-sm text-blue-600 dark:text-blue-400">Mastery %</p>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-200">{flashcardProgress.mastery_percentage.toFixed(1)}%</p>
              </div>
              <div className="bg-purple-50 dark:bg-purple-900 rounded-lg p-4">
                <p className="text-sm text-purple-600 dark:text-purple-400">Retention</p>
                <p className="text-2xl font-bold text-purple-900 dark:text-purple-200">{flashcardProgress.retention_rate.toFixed(1)}%</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Reviews (30 days)</p>
                <p className="text-xl font-bold text-gray-900 dark:text-white">{flashcardProgress.total_reviews_period}</p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Average Rating</p>
                <p className="text-xl font-bold text-gray-900 dark:text-white">{flashcardProgress.average_rating.toFixed(2)}/5</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        )}
      </div>
    );
  }

  if (flashcardMode === 'schedule') {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-6">
          <button onClick={() => setFlashcardMode('list')} className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
            <ArrowLeft size={20} />
          </button>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Study Schedule</h2>
        </div>

        {studySchedule ? (
          <div className="space-y-4">
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Period</p>
              <p className="text-lg font-bold text-gray-900 dark:text-white">{studySchedule.period_days} days</p>
            </div>
            <div className="bg-orange-50 dark:bg-orange-900 rounded-lg p-4">
              <p className="text-sm text-orange-600 dark:text-orange-400">Total Due Cards</p>
              <p className="text-lg font-bold text-orange-900 dark:text-orange-200">{studySchedule.total_due_cards}</p>
            </div>

            <h3 className="font-semibold text-gray-900 dark:text-white mt-6">Daily Schedule</h3>
            <div className="space-y-2">
              {Object.entries(studySchedule.daily_schedule).map(([date, dayData]) => (
                <div key={date} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <span className="text-gray-900 dark:text-white">{date}</span>
                  <span className={`font-semibold ${
                    dayData.due_count > 0 ? 'text-orange-600 dark:text-orange-400' : 'text-gray-600 dark:text-gray-400'
                  }`}>
                    {dayData.due_count} cards due
                  </span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        )}
      </div>
    );
  }

  if (reviewMode && reviewCards && reviewCards.length > 0) {
    const card = reviewCards[currentCardIndex];
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Review Mode</h2>
          <button
            onClick={() => { setReviewMode(false); setFlashcardMode('list'); }}
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

  return null;
}
