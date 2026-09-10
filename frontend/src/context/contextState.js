import React, { memo } from 'react'
import GlobalContext from './context'
import useCombineState from './combineState'

const ContextState = ({ children }) => {
  const combinedState = useCombineState()

  return (
    <GlobalContext.Provider value={combinedState}>
      {children}
    </GlobalContext.Provider>
  )
}

export default memo(ContextState)
